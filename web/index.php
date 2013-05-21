<?php


define('DB_FILE', '/tmp/habib.db');


// calculate Levenshtein distance between words w1 and w2

function zlevenshtein($w1, $w2)
{
    $l1 = len(w1);
    $l2 = len(w2);

    if ($l1 == 0)
        return $l2;

    if ($l2 == 0)
        return $l1;


    // test if last characters of the strings match

    $cost = ($w1[l1 - 1] == $w2[l2 - 1]) ? 0 : 1;

    
    // return minimum of delete char from w1, delete char from w2,
    // and delete char from both

    return min(levenshtein(substr($w1, 0, -1), $w2) + 1,
               levenshtein($w1, substr($w2, 0, -1)) + 1,
               levenshtein(substr($w1, 0, -1), substr($w2, 0, -1)) + $cost);
}


function get_similarity_score($phrase1, $phrase2)
{
    
    if (gettype($phrase1) == "string")
        $phrase1 = array_map('trim', explode(" ", $phrase1));

    if (gettype($phrase2) == "string")
        $phrase2 = array_map('trim', explode(" ", $phrase2));

    $score = 0;
    
    foreach ($phrase1 as $w1) {
        $s = 0;

        foreach ($phrase2 as $w2)
            $s = max(exp(-levenshtein(strtolower($w1), strtolower($w2))), $s);

        $score += $s;
    }

    return $score;
}


function cmp($a, $b)
{
    return ($a['score'] < $b['score']) ? 1 : -1;
}


function build_comparator($key)
{
    return function($a, $b) use ($key) {
        $score1 = $score2 = 0;        
        $score1 = get_similarity_score($a[1], $key);
        $score2 = get_similarity_score($b[1], $key);
        printf("a: %s<br>", $a[1]);
        printf("b: %s<br>", $b[1]);
        printf("key: %s, scores: %f  %f<br>", $key, $score1, $score2);
        $a[2] = $score1;
        $b[2] = $score2;
        
        return ($score1 < $score2) ? 1 : -1;
    };
}


printf('
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Фільм Хабібуліна</title>
    <link rel="stylesheet" type="text/css" media="screen" href="css/master.css" />
    <!-- script type="text/javascript"
            src="http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js"></script -->

    <link rel="stylesheet" href="http://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css" />
    <script src="http://code.jquery.com/jquery-1.9.1.js"></script>
    <script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
    <link rel="stylesheet" href="/resources/demos/style.css" />
    <script>
      $(function() {
      $( "input[type=submit], button" )
      .button()
      .click(function( event ) {
      event.preventDefault();
      });
      });
    </script>
    
  </head>
  <body>

    <div id="top">
      <div id="siteref"><a href="http://yahoo.com">Go home</a>
      </div>
    </div>
    
    <div id="query-area">
      <div id="title-area">
        <h1>Фільм Хабібуліна</h1>
        <h2>Цитатник Леся Подерв\'янського</h2>
      </div>
      <div>
        <form>
          <input name="query" />
          <input type="submit" value="GO!">
        </form>
      </div>
    </div>
    
    <div id="hint-area">
      <div class="hint-title">Example queries</div>
      
      <div class="hint">
        <a class="hint-link" href="http://yahoo.com">От де екзистенція</a>
      </div>
      
      <div class="hint">
        <a class="hint-link" href="http://yahoo.com">дослідники калу</a>
      </div>
      
    </div>
    
    <div id="result-area">
');


// open the database

if (!file_exists(DB_FILE)) {
    printf("ERROR: no database");
    exit(1);
}

if (!($db = new SQLite3(DB_FILE, SQLITE3_OPEN_READONLY))) {
    printf("ERROR: cannot open database");
    exit(1);
}


// load tokens

$query = "пизділи тьолок";
$query = "дослідники калу";

$phrases = array();

//$st = @$db->query("SELECT quote_id, tokens FROM quotes where play_id == 12");
$st = @$db->query("SELECT quote_id, tokens FROM quotes");

while ($row = $st->fetchArray()) {
    array_push($phrases, array('quote_id' => $row[0], 'tokens' => $row[1],
                               'score' => get_similarity_score($row[1], $query)));
}


// collect top 5 matches

usort($phrases, 'cmp');

$quote_ids = array();
$ii = 0;

foreach ($phrases as $key => $value) {
    if ($ii > 5 || $value['score'] < 0.05)
        break;

    array_push($quote_ids, $value['quote_id']);
    $ii++;
}

if (count($quote_ids) == 0) {
    print "<b>NO MATCHES</b>";
    exit(1);
}


$st = $db->query("
SELECT quote_id, title, url, speaker, phrase
    FROM plays AS p, quotes AS q
    WHERE q.play_id == p.play_id
        AND q.quote_id IN (" . implode(", ", $quote_ids) . ")");

$results = array();

while ($row = $st->fetchArray()) {
    $results[$row['quote_id']] = $row;
}

foreach ($quote_ids as $quote_id) {
    $row = $results[$quote_id];
    printf('
      <div class="result-entry">
        <a class="source-link" href="%s">%s</a>
        <p class="quote"><span class="speaker">%s</span>
          %s
        </p>
      </div>
', $row['url'], $row['title'], $row['speaker'], $row['phrase']);
}



printf('
      
    </div>
    
    <div id="bottom">
      <div id="siteref"><a href="http://yahoo.com">About</a>
      </div>
    </div>
    
  </body>
</html>
');



?>