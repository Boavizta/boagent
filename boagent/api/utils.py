from dateutil import parser

def iso8601_or_timestamp_as_timestamp(iso_time: str):
    '''
    Takes an str that's either a timestamp or an iso8601
    time. Returns a float that represents a timestamp.
    '''
    if iso_time == "0.0" or iso_time == "0":
        return float(iso_time)
    else:
        dt = None
        try:
            dt = parser.parse(iso_time)
            print("{} is an iso 8601 datetime".format(iso_time))
        except Exception as e:
            print("{} is not an iso 8601 datetime".format(iso_time))
            print("Exception : {}".format(e))
            try:
                dt = datetime.fromtimestamp(int(round(float(iso_time))))
                print("{} is a timestamp".format(iso_time))
            except Exception as e:
                print("{} is not a timestamp".format(iso_time))
                print("Exception : {}".format(e))
                print("Parser would give : {}".format(parser.parse(iso_time)))
        finally:
            if dt:
                return dt.timestamp()
            else:
                return float(iso_time)

