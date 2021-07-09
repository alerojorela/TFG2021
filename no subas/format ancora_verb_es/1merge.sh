#!/bin/bash
# echo <?xml version="1.0" encoding="UTF-8"?> > merged.xml
echo > merged.xml
for filename in ancora-verb-es/*.xml; do
    xmlstarlet sel -B -t -c 'lexentry' "$filename" >> merged.xml
    echo >> merged.xml
done

# xmlstarlet sel -B -t -c 'lexentry' aullar.lex.xml
