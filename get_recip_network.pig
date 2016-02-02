data = LOAD '$in' USING PigStorage('\t') AS (toID:long, fromID:long, cnt:long);

--- filter out looping edges
data = FILTER data BY toID != fromID;

--- get mirror reading
data = FOREACH data GENERATE toID AS toID:long, fromID AS fromID:long;
data_mirror = FOREACH data GENERATE fromID AS toID:long, toID AS fromID:long;

--- set intersection operation of mirrored edges
cgrp = COGROUP data by (toID, fromID), data_mirror by (toID, fromID);
--- set intersection requires both cogroup to exist
intersect = FILTER cgrp BY NOT IsEmpty(data) and NOT IsEmpty(data_mirror); 

--- organize results
result = FOREACH intersect GENERATE FLATTEN(group) AS (IDONE:long, IDTWO:long);
result = ORDER result BY IDONE, IDTWO;

--- write to HDFS
STORE result into '$out' USING PigStorage('\t', '-schema');
