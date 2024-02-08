# Contributing to the project

## Prerequisites

The data processing and validation tools in this repository require:

-   Bash
-   Gnu Make
-   Grep
-   JQ
-   Python3
-   Virtualenv
-   Additional Python packages listed in `tools/requirements.txt`

In addition, the optional image generation tools require:

-   Chromedriver

On a Debian-like operating system, these prerequisites can be installed with:


```
sudo apt install \
   bash make grep jq python3 virtualenv \
   chromium-chromedriver
```


## Initial set up

### Environment

In Bash, set up a virtual Python environment and install necessary packages:

```
virtualenv -p python3 .venv
.venv/bin/python3 -m pip install -r tools/requirements.txt
```


### Validation

Validate existing files, in parallel, using all available cores:

```
make -j validate
```

The first time this is run it will take some time and generate a lot of output.


### View tasks

```
make task
```

This command will print out a list of:

-   Predicted upcoming fairs to investigate and add to the repository
-   Known fairs for which exhibitor lists may have become available
-   Known fairs for which exhibitor list sources should be checked for updates


## Adding data

JSON data should be added, one file per event, in a path like `data/<slug>-<year>.json`, where:

-   `<year>` is the four-digit year of the event's data
    -   For postponed events, use the year of the original intenteded date.
-   `<slug>` is a short form of the fair' series name
    -   Use only lowercase-alpha, numeric and hyphen characters
    -   Search the existing data and use slugs for the same series if they already exist
    -   When series change their name, we update all previous slugs to match the new name
        Eg. `hdse-2017` was changed to `3cdse-2017` when the series changed name in 2018.

The JSON data must match the schema defined in `schema/fair.schema.json`. The validation command above will fail for any fairs where this is not the case.

CSV data is permitted, one file per event, in the form `data/<slug>-<year>.csv`.

-   Use consistent quoting for CSV formats. Either all fields should be quoted or none should be.
-   If choosing not to quote any fields, semicolons may be preferred as delimiters as they seldom occur in source data


