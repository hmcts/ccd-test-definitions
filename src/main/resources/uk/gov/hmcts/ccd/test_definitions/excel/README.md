## :warning: WARNING

These Excel files **should not be** imported directly into an environment as they contain callback URLs
that are in a templated format: `${ENV_VAR:http://default.value}/rest_of_url_path`.  Without these URLs being correctly
processed by the [BEFTA Framework](https://github.com/hmcts/befta-fw) into valid values will result in any attempt to
trigger the related case events to fail.  

> **Note: Importing these raw Excel files into a higher-level environment may 
cause in-flight pipelines running against that environment to fail.**

For further information on how to test locally using case definitions from these files see 
[Generating definition files without templated URLs](../../../../../../../../../README.md#generating-definition-files-without-templated-urls)
or [Testing locally](../../../../../../../../../README.md#testing-locally).

