# INDICES WEIGHTAGE SCRAPPER

A scrapper to get weightage of stock in different indices from NIFTYINDICES https://www.niftyindices.com.
Scrapper is made using asyncio to get most speed possible from server (which is really fast).
Number of concurrent requests is limited by `Semaphore`, one can change its value to own needs but higher values are susceptible to timeout errors.
