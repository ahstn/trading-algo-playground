## Hyperliquid TradingView Connector

> [!NOTE]
>
> See [hyperliquid-python-sdk | GitHub] for documentation and authentication setup. 

> [!WARNING]
>
> In this repository, authentication isn't setup correctly and is un-documented on purpose, see the above repo instead.

## Function Deployment

For an updated walkthough, see [Deploy HTTP Function with Python | Google Docs]

```sh
gcloud functions deploy <function name> \
    --gen2 \
    --runtime=python310 \
    --region=us-west1 \
    --source=. \
    --entry-point=<main function name> \
    --trigger-http \
    --project <gcloud project name>
```

## Local Testing

[functions-framework-python] exposes a local helper for running your function and listening on port `8080`:

```sh
functions-framework-python --target hyper_http

curl --request POST \
  --url http://localhost:8080/ \
  --data '{
    "action": "buy",
    "ticker": "ETHUSDT",
    "position": "buy",
    "price": 3811.37
  }'
```

Keep in mind, if your code is pointed to the "live" exchange, and not the "testnet", this will execute "real" trades.


## State Machine

```mermaid
graph TD
    Start --> IsPositionFlat{Webook JSON<br>Desired Position == Flat?}

    IsPositionFlat -->|Yes| HasExistingPosition{Check Exchange<br>Has Existing Position?}
    HasExistingPosition -->|Yes| ClosePosition[Close Existing Position<br>Cancel Orders]
    HasExistingPosition -->|No| NoAction[No Action Required]

    IsPositionFlat -->|No| IsPositionOpen{Webook JSON<br>Previous Position == Flat?}
    IsPositionOpen -->|Yes| OpenPosition[Open New Position]
    IsPositionOpen -->|No| IsReversingPosition{Webook JSON<br>Reversing Position?}

    IsReversingPosition -->|Yes| HasMatchingPosition{Check Exchange<br>Has Matching Position?}
    HasMatchingPosition -->|Yes| ReversePosition[Reverse Position with Double Size<br>Cancel Orders]
    HasMatchingPosition -->|No| OpenNewPosition[Open New Position]

    IsReversingPosition -->|No| AdjustPosition[Adjust Existing Position<br>Cancel Orders<br>Ensure reduce_only = true]

    ClosePosition --> FinishOrder
    NoAction --> FinishOrder
    OpenPosition --> FinishOrder
    ReversePosition --> FinishOrder
    OpenNewPosition --> FinishOrder
    AdjustPosition --> FinishOrder
    FinishOrder[Finish Order Execution]
```

[functions-framework-python]: https://github.com/GoogleCloudPlatform/functions-framework-python
[Deploy HTTP Function with Python | Google Docs]: https://cloud.google.com/functions/docs/create-deploy-http-python
[hyperliquid-python-sdk | GitHub]: https://github.com/hyperliquid-dex/hyperliquid-python-sdk