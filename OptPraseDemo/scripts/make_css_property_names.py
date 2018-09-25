#!/usr/bin/env python

import os.path
import re
import subprocess
import sys

from in_file import InFile
import in_generator
import license
from functools import reduce


HEADER_TEMPLATE = """
%(license)s

#ifndef %(class_name)s_h
#define %(class_name)s_h

#include "core/css/CSSParserMode.h"
#include "wtf/HashFunctions.h"
#include "wtf/HashTraits.h"
#include <string.h>

#define ENABLE_EXPAND_HTML 0
namespace WTF {
class AtomicString;
class String;
}

namespace WebCore {

enum CSSPropertyID {
    CSSPropertyInvalid = 0,
    CSSPropertyVariable = 1,
%(property_enums)s
};

const int firstCSSProperty = %(first_property_id)s;
const int numCSSProperties = %(properties_count)s;
const int lastCSSProperty = %(last_property_id)d;
const size_t maxCSSPropertyNameLength = %(max_name_length)d;

const char* getPropertyName(CSSPropertyID);
const WTF::AtomicString& getPropertyNameAtomicString(CSSPropertyID);
WTF::String getPropertyNameString(CSSPropertyID);
WTF::String getJSPropertyName(CSSPropertyID);
bool isInternalProperty(CSSPropertyID id);

inline CSSPropertyID convertToCSSPropertyID(int value)
{
    ASSERT((value >= firstCSSProperty && value <= lastCSSProperty) || value == CSSPropertyInvalid);
    return static_cast<CSSPropertyID>(value);
}

} // namespace WebCore

namespace WTF {
template<> struct DefaultHash<WebCore::CSSPropertyID> { typedef IntHash<unsigned> Hash; };
template<> struct HashTraits<WebCore::CSSPropertyID> : GenericHashTraits<WebCore::CSSPropertyID> {
    static const bool emptyValueIsZero = true;
    static const bool needsDestruction = false;
    static void constructDeletedValue(WebCore::CSSPropertyID& slot) { slot = static_cast<WebCore::CSSPropertyID>(WebCore::lastCSSProperty + 1); }
    static bool isDeletedValue(WebCore::CSSPropertyID value) { return value == (WebCore::lastCSSProperty + 1); }
};
}

#endif // %(class_name)s_h
"""

GPERF_TEMPLATE = """
%%{
%(license)s

#include "config.h"
#include "%(class_name)s.h"
#include "core/css/HashTools.h"
#include <string.h>

#include "wtf/ASCIICType.h"
#include "wtf/text/AtomicString.h"
#include "wtf/text/WTFString.h"

namespace WebCore {
static const char propertyNameStringsPool[] = {
%(property_name_strings)s
};

static const unsigned short propertyNameStringsOffsets[] = {
%(property_name_offsets)s
};

%%}
%%struct-type
struct Property;
%%omit-struct-type
%%language=C++
%%readonly-tables
%%global-table
%%compare-strncmp
%%define class-name %(class_name)sHash
%%define lookup-function-name findPropertyImpl
%%define hash-function-name propery_hash_function
%%define slot-name nameOffset
%%define word-array-name property_wordlist
%%enum
%%%%
%(property_to_enum_map)s
%%%%
const Property* findProperty(register const char* str, register unsigned int len)
{
    return %(class_name)sHash::findPropertyImpl(str, len);
}

const char* getPropertyName(CSSPropertyID id)
{
    if (id < firstCSSProperty)
        return 0;
    int index = id - firstCSSProperty;
    if (index >= numCSSProperties)
        return 0;
    return propertyNameStringsPool + propertyNameStringsOffsets[index];
}

const AtomicString& getPropertyNameAtomicString(CSSPropertyID id)
{
    if (id < firstCSSProperty)
        return nullAtom;
    int index = id - firstCSSProperty;
    if (index >= numCSSProperties)
        return nullAtom;

    static AtomicString* propertyStrings = new AtomicString[numCSSProperties]; // Intentionally never destroyed.
    AtomicString& propertyString = propertyStrings[index];
    if (propertyString.isNull()) {
        const char* propertyName = propertyNameStringsPool + propertyNameStringsOffsets[index];
        propertyString = AtomicString(propertyName, strlen(propertyName), AtomicString::ConstructFromLiteral);
    }
    return propertyString;
}

String getPropertyNameString(CSSPropertyID id)
{
    // We share the StringImpl with the AtomicStrings.
    return getPropertyNameAtomicString(id).string();
}

String getJSPropertyName(CSSPropertyID id)
{
    char result[maxCSSPropertyNameLength + 1];
    const char* cssPropertyName = getPropertyName(id);
    const char* propertyNamePointer = cssPropertyName;
    if (!propertyNamePointer)
        return emptyString();

    char* resultPointer = result;
    while (char character = *propertyNamePointer++) {
        if (character == '-') {
            char nextCharacter = *propertyNamePointer++;
            if (!nextCharacter)
                break;
            character = (propertyNamePointer - 2 != cssPropertyName) ? toASCIIUpper(nextCharacter) : nextCharacter;
        }
        *resultPointer++ = character;
    }
    *resultPointer = '\\0';
    return String(result);
}

bool isInternalProperty(CSSPropertyID id)
{
    switch (id) {
        %(internal_properties)s
            return true;
        default:
            return false;
    }
}

} // namespace WebCore
"""


class CSSPropertiesWriter(in_generator.Writer):
    class_name = "CSSPropertyNames"
    defaults = {
        'alias_for': None,
        'is_internal': False,
    }

    def __init__(self, file_paths):
        in_generator.Writer.__init__(self, file_paths)
        self._outputs = {(self.class_name + ".h"): self.generate_header,
                         (self.class_name + ".cpp"): self.generate_implementation,
                        }
        #print(('[__init__] name_dictionaries:', self.in_file.name_dictionaries))
        self._aliases = [property for property in self.in_file.name_dictionaries if property['alias_for']]
        for offset, property in enumerate(self._aliases):
            # Aliases use the enum_name that they are an alias for.
            property['enum_name'] = self._enum_name_from_property_name(property['alias_for'])
            # Aliases do not get an enum_value.

        self._properties = [property for property in self.in_file.name_dictionaries if not property['alias_for']]
        if len(self._properties) > 1024:
            print("ERROR : There is more than 1024 CSS Properties, you need to update CSSProperty.h/StylePropertyMetadata m_propertyID accordingly.")
            exit(1)
        self._first_property_id = 2  # We start after CSSPropertyInvalid and CSSPropertyVariable.
        property_id = self._first_property_id
        offset = 0
        for num, property in enumerate(self._properties):
            property['enum_name'] = self._enum_name_from_property_name(property['name'])
            if(self._enum_name_from_property_name(property['name']).startswith("#")):
                continue
            property['enum_value'] = self._first_property_id + offset
            if property['name'].startswith('-internal-'):
                property['is_internal'] = True
            offset+=1

    def _enum_name_from_property_name(self, property_name):
        print(('[_enum_name_from_property_name] property_name:', property_name))
        if(property_name.startswith("#")):
            return property_name
        return "CSSProperty" + re.sub(r'(^[^-])|-(.)', lambda match: (match.group(1) or match.group(2)).upper(), property_name)

    def _enum_declaration(self, property):
        print('[_enum_declaration] property:', property['name'])
        if(property['name'].startswith('#')):
            return property['name']
        return "    %(enum_name)s = %(enum_value)s," % property

    def generate_header(self):
        print('[generate_header] self._properties:', self._properties)
        return HEADER_TEMPLATE % {
            'license': license.license_for_generated_cpp(),
            'class_name': self.class_name,
            'property_enums': "\n".join(map(self._enum_declaration, self._properties)),
            'first_property_id': self._first_property_id,
            'properties_count': len(self._properties),
            'last_property_id': self._first_property_id + len(self._properties) - 1,
            'max_name_length': reduce(max, list(map(len, [property['name'] for property in self._properties]))),
        }

    def _case_properties(self, property):
        return "case %(enum_name)s:" % property

    def generate_implementation(self):
        property_offsets = []
        current_offset = 0
        for property in self._properties:
            property_offsets.append(current_offset)
            current_offset += len(property["name"]) + 1

        gperf_input = GPERF_TEMPLATE % {
            'license': license.license_for_generated_cpp(),
            'class_name': self.class_name,
            'property_name_strings': '\n'.join(['    "%(name)s\\0"' % property for property in self._properties]),
            'property_name_offsets': '\n'.join(['    %d,' % offset for offset in property_offsets]),
            'property_to_enum_map': '\n'.join(['%(name)s, %(enum_name)s' % property for property in self._properties + self._aliases]),
            'internal_properties': '\n'.join(map(self._case_properties, [property for property in self._properties if property['is_internal']])),
        }
        # FIXME: If we could depend on Python 2.7, we would use subprocess.check_output
        gperf_args = ['gperf', '--key-positions=*', '-P', '-D', '-n', '-s', '2']
        gperf = subprocess.Popen(gperf_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return gperf.communicate(gperf_input)[0]


if __name__ == "__main__":
    #sys.argv[1] = 'CSSPropertyNames.in';
    #sys.argv[2] = '--output_dir \"blink\" --defines \"ENABLE_EXPAND_HTML=0\"';
    print('[argv] sys.argv:', sys.argv[0])
    in_generator.Maker(CSSPropertiesWriter).main(sys.argv)
