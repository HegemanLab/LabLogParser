`HyStarErrLogbook.log` thoughts:
  * Lines which do not start with a timestamp should be concatenated to the previous line
    * eg. line 14 and 15 should be one line in the [error log](https://github.umn.edu/HegemanLab/ELK-MS/blob/master/example-logs/hystar-logs/HyStarErrLogbook.log)
  * Fields to collect per log
    * Timestamp (date-time)
    * Message
    * Message hash
      * Do this once the first two are working well


