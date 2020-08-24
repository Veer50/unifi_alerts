# UniFi Alerts

"This module generates Unifi_alerts on sensor-alarms index on regular basis at the end of a day"


# Installation

If you don't use `pipsi`, you're missing out.
Here are [installation instructions](https://github.com/mitsuhiko/pipsi#readme).

Simply run:

    $ pipsi install .


# Usage

To use it:

    $ unifi-alerts --help

    unifi-alerts "{\"venue_config\":{\"tz_region\":\"Asia/Kolkata\",\"venue_id\":\"80736d3841be43eb84468e90d310a931\"},\"elastic_config\":{\"host\":\"https://4108c6550bc044ceb7a6271dad0ee17f.europe-west1.gcp.cloud.es.io\",\"port\":9243,\"username\":\"elastic\",\"password\":\"0p8iGL2ZbyOvn8Vk1CIeYHy9\",\"index_prefix\":\"sensor-alarms-*\"},\"email_config\":{\"sender\":\"veertest50@gmail.com\",\"password\":\"password\",\"recipient\":\"veereshp@intelipower.co.za\",\"sub\":\"Unifi alerts\",\"body\":\"Hi, \n\n Kindly find the attached file of Unifi Alerts.\"}}"
