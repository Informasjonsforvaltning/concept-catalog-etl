# ConceptDeleter

Build: mvn install

Usage: java -jar concept-deleter-1.0.0-SNAPSHOT.jar \<file of line-separated concept identifiers\> \<FDK concept endpoint\> \<concept endpoint username\> \<concept endpoint password\> \<elastic-search endpoint URL\> \<GCP elastic port-forward cookie value\>

Example Usage: java -jar concept-deleter-1.0.0-SNAPSHOT.jar "./fdk.extra.guid" "https://fellesdatakatalog.brreg.no/api/concepts" "" "" "https://9200-dot-6819558-dot-devshell.appspot.com" "bad6aa6e6ffc31c5bc86f1b778c6a78cb8b8ae13391c484ac18b00cb7de40add"

(Information on how to expose GCP ElasticSearch instance by port-forwarding is available at https://confluence.brreg.no/display/INFFOR/Legge+inn+nye+publishere )

Example on how to get identifiers for Skatteetaten concepts:

First, get the ones already present in FDK (page size 1000 is maximum. There are currently 3252 concepts):

`curl -s "https://fellesdatakatalog.brreg.no/api/concepts?publisher=974761076&size=1000&page=0" > /tmp/974761076.xml`

`curl -s "https://fellesdatakatalog.brreg.no/api/concepts?publisher=974761076&size=1000&page=1" >> /tmp/974761076.xml`

`curl -s "https://fellesdatakatalog.brreg.no/api/concepts?publisher=974761076&size=1000&page=2" >> /tmp/974761076.xml`

`curl -s "https://fellesdatakatalog.brreg.no/api/concepts?publisher=974761076&size=1000&page=3" >> /tmp/974761076.xml`

`cat /tmp/974761076.xml |jq .|grep "\"identifier\":"|grep "http://begrepskatalogen/begrep/"|cut -c 24-90|sort > fdk.guid`
 
Then, get the ones from Skatteetaten and adjust to same identifier format:

`curl -s https://data.skatteetaten.no/begreper/ | tidy -xml -i -q -|grep "<identifier>"|cut -c 17-52|sort|sed -e 's/^/http:\/\/begrepskatalogen\/begrep\//' > skatteetaten.guid`

To remove concepts from FDK that is not present in Skatteetaten, compare the files and keep ids only present in FDK. (If you name this file fdk.extra.guid you can call concept-deleter as in Example Usage above)
