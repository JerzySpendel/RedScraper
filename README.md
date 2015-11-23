RedScraper
=========

Redscraper is a simple library to write scrapping data crawlers.

You can try this running example.py or by creating new project by redscraper.py -n project_name

To run any project you have to have runnig redis service on localhost (or somewhere else but it will be slow) defaultly on 6379 port.
Running new project without any flags will populate redis database with initial url, you can avoid this by running project with --slave flag, and you should do this if you want to run scrapping in parallel on many machines