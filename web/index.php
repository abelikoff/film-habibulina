<?php

  /*
    Copyright (C) 2013, Alexander L. Belikoff  ( http://belikoff.net )
    
    This file is part of the project "Film Habibulina".
    
    Film Habibulina is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.
    
    Film Habibulina is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with the project.  If not, see <http://www.gnu.org/licenses/>.
  */

require_once('config.php');


function show_error($external_msg, $internal_msg)
{
    printf('
          <div class="alert alert-error">
            <strong>ERROR:</strong> %s
          </div>
', htmlspecialchars($external_msg));

    error_log($internal_msg);
}


function show_matches($query, $show_scores = FALSE)
{
    // open the database

    if (!file_exists(DB_FILE)) {
        show_error("Database problem (Щас ні в них, ні в нас, кругом порядка нема)",
                   sprintf("DB file %s is missing", DB_FILE));
        return;
    }

    if (!($db = new SQLite3(DB_FILE, SQLITE3_OPEN_READONLY))) {
        show_error("Database problem (Щас ні в них, ні в нас, кругом порядка нема)",
                   sprintf("Failed to open DB file %s", DB_FILE));
        return;
    }


    // load tokens
    
    $phrases = array();
    $st = @$db->query("SELECT quote_id, tokens FROM quotes");

    while ($row = $st->fetchArray()) {
        array_push($phrases, array('quote_id' => $row[0], 'tokens' => $row[1],
                                   'score' => get_similarity_score($query, $row[1])));
    }


    // collect top 5 matches

    usort($phrases, 'cmp');
    $quote_ids = array();
    $scores = array();
    $ii = 0;
    
    foreach ($phrases as $key => $value) {
        $ii++;

        if ($ii > 5 || $value['score'] < SCORE_CUTOFF)
            break;
        
        array_push($quote_ids, $value['quote_id']);
        $scores[$value['quote_id']] = $value['score'];
    }

    if (count($quote_ids) == 0) {
        print "<b>NO MATCHES</b>"; /* FIXME */
        return;
    }

    print('
    <div id="results-area">
');


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
        $speaker = $row['speaker'];

        if ($speaker != "")
            $speaker .= ":";
        
        printf('
      <div class="result-entry">
        <a class="source-link" href="%s" target="_blank">%s</a>
        <div class="quote"><span class="speaker">%s</span>
          %s
        </div>
', $row['url'], $row['title'], $speaker, $row['phrase']);

        if ($show_scores)
            printf('<span class="score">%.5f</span>', $scores[$quote_id]);
            
        printf('
      </div>
');
    }

    print('
    </div>  <!-- results-area -->
');
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

        foreach ($phrase2 as $w2) {
            $scale = max(strlen($w1), strlen($w2));
            $s = max(exp(- RATE * levenshtein(strtolower($w1), strtolower($w2)) / $scale), $s);
        }

        $score += $s;
    }

    return $score;
}


function cmp($a, $b)
{
    return ($a['score'] < $b['score']) ? 1 : -1;
}



// parse input

$query = "";

if (isset($_REQUEST['query']))
    $query = trim($_REQUEST['query']);


printf('
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Фільм Хабібуліна</title>
    <link href="http://fonts.googleapis.com/css?family=Roboto+Slab&subset=latin,cyrillic"
                 rel="stylesheet" type="text/css">

    <link rel="stylesheet" type="text/css" href="master.css" />
    <script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
    <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js"></script>
    <link rel="stylesheet" type="text/css"
      href="http://code.jquery.com/ui/1.9.1/themes/smoothness/jquery-ui.css" />
    <link href="http://netdna.bootstrapcdn.com/twitter-bootstrap/2.3.2/css/bootstrap-combined.min.css" rel="stylesheet" />
    <script src="http://netdna.bootstrapcdn.com/twitter-bootstrap/2.3.2/js/bootstrap.min.js"></script>
    <!--script src="http://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/2.3.1/js/bootstrap.min.js"></script>
    <link href="http://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/2.3.1/css/bootstrap.min.css" rel="stylesheet" / -->
  </head>
  <body>

    <div id="top" class="for-screen-only">
      <a href="https://github.com/abelikoff/film-habibulina"><img style="position: absolute; top: 0; left: 0; border: 0;" src="https://s3.amazonaws.com/github/ribbons/forkme_left_gray_6d6d6d.png" alt="Fork me on GitHub" /></a>
    </div>

    <div id="query-area">
      <div id="title-area">
        <a id="titleref" href="%s"><h1>Фільм&nbsp;Хабібуліна</h1></a>
        <h2>Цитатник&nbsp;Леся&nbsp;Подерв\'янського</h2>
      </div>
      <div id="input-area">
        <form action="">
          <input class="input-medium search-query" type="text" name="query" value="%s" />
          <button class="btn btn-primary">Поиск</button>
        </form>
      </div>
    </div> <!-- query-area -->

',
       sprintf("http://%s%s", $_SERVER['HTTP_HOST'], $_SERVER['PHP_SELF']),
       htmlspecialchars($query));


if ($query != "") {
    $show_score = isset($_REQUEST['show_score']);
    show_matches($query, $show_score);
}
else {
    $examples = array('От де екзистенція',
                      'дослідники калу',
                      'Шо за ностальгія, чого вам щас не хвата, тюрми?',
                      'Я ето не люблю',
                      'Шо мовчите, скуштували хуя?',
                      'А ти хуй в бєлки видів?',
                      'День колгоспника',
                      'Йобане село',
                      'Така робота, шо нема шо спиздить');

    $selected = array_rand($examples, 3);

    printf('
    <div id="hint-area">
      <div class="hint-title">Example queries</div>
      <ul>
');
      
    foreach ($selected as $str) {
        $url = sprintf("http://%s%s?%s",
                       $_SERVER['HTTP_HOST'],
                       $_SERVER['PHP_SELF'],
                       http_build_query(array('query' => $examples[$str])));
        printf('
        <li class="hint">
          <a class="hint-link" href="%s">%s</a>
        </li>

', $url, $examples[$str]);
    }
    
    printf('

      </ul>
    </div>   <!-- hint-area -->
');


}

printf('

    </div>

    <footer>
      <hr />
      <div id="credits">Текст произведений Леся: 
        <a href="http://www.doslidy.kiev.ua/" target="_blank">doslidy.kiev.ua</a>
      </div>

      <div id="siteref">Yet another contribution to humanity
        by <a href="http://belikoff.net" target="_blank">Alexander L. Belikoff</a>
      </div>
    </footer>

  </body>
</html>
');



?>