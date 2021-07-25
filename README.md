# tap-simpleanalytics

A singer.io tap for extracting data from the [Simple Analytics](https://www.simpleanalytics.com) API written in python 3.

Author: Hugh Nimmo-Smith (hugh@ideavate.co.uk)

## Data extracted

- `visits` using v2 API

## Configuration

The following keys are required:

```json
{
  "sa_hostnames": ["yourdomin.com", "sub.yourdomain.com"],
  "sa_user_id": "sa_user_id_00000000-0000-0000-0000-000000000000",
  "sa_api_key": "sa_api_key_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "sa_start_date": "2020-01-01"
}
```
