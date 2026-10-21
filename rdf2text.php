<?php
include 'vendor/autoload.php';
use rdfInterface\Literal;

if ($argc < 3) {
    exit("Usage: " . $argv[0] . " inputFile outputFile\n");
}
$df = new quickRdf\DataFactory();
$idProp = $df->namedNode('https://vocabs.acdh.oeaw.ac.at/schema#hasIdentifier');
$titleProp = $df->namedNode('https://vocabs.acdh.oeaw.ac.at/schema#hasTitle');

// maps arche API URIs to a path part of identifier in the https://id.acdh.oeaw.ac.at namespace
$uri2title = [];
$iterator = quickRdfIo\Util::parse($argv[1], $df);
foreach ($iterator as $triple) {
    if ($triple->getPredicate()->equals($titleProp)) {
        $uri2title[(string) $triple->getSubject()] = (string) $triple->getObject();
    }
}

$output = fopen($argv[2], 'w');
$iterator = quickRdfIo\Util::parse($argv[1], $df);
foreach ($iterator as $triple) {
    $subject   = (string) $triple->getSubject();
    $predicate = (string) $triple->getPredicate();
    $object    = $triple->getObject();

    $subject = parse_url($subject, PHP_URL_PATH);

    $predicate = parse_url($predicate, PHP_URL_FRAGMENT);
    $predicate = str_replace(['has', 'isPart', 'By'], ['has ', 'is part ', ' by'], $predicate);
    $predicate = strtolower($predicate);

    if ($object instanceof Literal) {
        $object = (string) $object;
    } else {
        $object = $uri2title[(string) $object] ?? (string) $object;
    }

    fwrite($output, "$subject $predicate $object.\n");
}
fclose($output);

