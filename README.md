This is a Fluent migration script designed to remove the technical burden of creating new migration recipes for Mozilla Thunderbird. The script crawls the source tree and finds unmigrated DTD files, along with any files that source the DTD file.

Recipe Factory builds on the awesome work of Zibi Braniecki's XUL-to-Fluent migration script (https://github.com/zbraniecki/convert_xul_to_fluent).

Installing:

```
pip3 install -r requirements.txt
```

Not yet added:
- JS dependency crawling
- DOM string sorting
- Side-by-side recipe tweaking
