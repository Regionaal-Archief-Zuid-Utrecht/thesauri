# RAZU thesauri

Thesauri in RDF for the RAZU e-depot / digital repository.

## How to use

1. Use the turtle files in the `rdf` directory for updating the concepts.

2. Run `python tools/validate.py` to validate the RDF against a SHACL profile.

3. Run `python tools/ttl2json.py` to convert the turtle files to json (the prefered format for the repository)

4. Run `python tools/storeS3.py` to upload the generated json files to the `context`bucket in the S3 store.

5. Upload the files to the relevant datasets in the triplestore. Currently done manually.
Each thesaurus has its own dataset in the Triply environment. Each thesaurus is also uploaded to the id/object dataset to allow all data to be queried from a single SPARQL endpoint.

## Requirements

Make sure to load the requirements from `requirements.txt` before running the scripts.
For `storeS3.py`, [Razulibs](https://github.com/Regionaal-Archief-Zuid-Utrecht/razulibs) should be in the `$PYTHONPATH` environment variable, or installed in your python environment.

## Environment configuration

Install dependencies
   
   ```bash
   pip install -r requirements.txt
   ```

Make sure razulibs is in `$PYTHONPATH`.

## TODO

- Automated upload to triplestore
