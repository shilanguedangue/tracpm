 
  
'''  
  
  SELECT 
  'MILESTONE'        as A,
  'NULL'             as B,
  name               as C,
  'NULL'             as D,
  'NULL'             as E,
  substr(due,1,10)   as F,
  substr(completed,1,10) as G
  FROM
  milestone
  WHERE
    completed = 0
    and
    substr(due, 1,10 ) 
  BETWEEN
   1348977600 and 1352610000
   UNION 
  SELECT  
  'TICKET'           as A,
  id                 as B,
  milestone          as C,
  summary            as D,
  status             as E,
  substr(time,1,10)   as F,
  substr(changetime,1,10) as G
  FROM
  ticket
  WHERE
    cast(substr(time, 1,10 ) as int) 
  BETWEEN
   1348977600 and 1352610000
   
   
'''