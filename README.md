# Trading Algo Playground

[![forthebadge](https://forthebadge.com/images/featured/featured-made-with-crayons.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/works-on-my-machine.svg)](https://forthebadge.com)

> [!WARNING]
>
> This repository is intended for educational purposes only. It is not intended to be used for live trading. Use at your own risk.

### Overview

This is a partial publication of a private repo. As such doesn't include live strategies or other sensitive information. 

Whilst it may contain references from non-public code, I'll attempt to keep this to a minimum and keep this repository up to date.

This repository contains the setup and configuration for two "systems":
- Boilerplate setup for [Freqtrade]
  - see [freqtrade/README.md] for technical information.
- Python [GCP Functions] for DEX trading from TradingView Webhooks
  - see [hyper/README.md] for technical information.

If you're unfamilar with [Freqtrade], [Quickstart with Docker | Freqtrade] is likely a better starting point.

### Freqtrade  

Freqtrade is a free, open source crypto trading bot written in Python. Built with CCXT it is designed to support all major exhanges while having great backtesting and strategy development tools. 


### Python GCP Functions

These are simple python script intended to be deployed to GCP Functions and listen for TradingView Webhooks. Upon receiving a webhook, the script will execute a trade based on the JSON body passed. 

As these are simple "executors", it's important you have a good understanding of your strategy and practice proper risk management with sizing.

[Freqtrade]: https://github.com/freqtrade/freqtrade
[GCP Functions]: https://cloud.google.com/functions
[TradingView Webhooks]: https://www.tradingview.com/support/solutions/43000529348-about-webhooks/
[Quickstart with Docker | Freqtrade]: https://www.freqtrade.io/en/stable/docker_quickstart/
[hyper/README.md]: [hyper/README.md]
[freqtrade/README.md]: [freqtrade/README.md]
[CCXT]: https://github.com/ccxt/ccxt