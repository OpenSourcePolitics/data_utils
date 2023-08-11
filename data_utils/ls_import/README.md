# ls_import
This script allows to send answers from a Limesurvey instance directly to a Postgres database.

## Howto
1. Setup your Limesurvey instance correctly : go to `Configuration > Global > Interface`, and enable `JSON-RPC` in menu `RPC interface enabled` and `Publish API on /admin/remotecontrol`. Save your settings
2. Fill a `.env` based on the `.env.example` of `data_utils/ls_import` with your Limesurvey credentials (run `cp ls_import/.env.example ls_import/.env` for such maneuver)
3. Run the script