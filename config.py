
import optparse
import configparser


def config_cmd():
    parser = optparse.OptionParser("%prog [options]") # 1st argument is usage, %prog is replaced with sys.argv[0]
    parser.add_option(
                      "-i", "--ip",
                      dest="ip",       # not needed in this case, because default dest name is derived from long option
                      type="string",       # "string" is default, other types: "int", "long", "choice", "float" and "complex"
                      action="store",      # "store" is default, other actions: "store_true", "store_false" and "append"
                      #default="localhost", # set default value here, None is used otherwise
                      help="IP address",
                      )
    parser.add_option(
                      "-p", "--port",    # short and long option
                      dest="port",       # not needed in this case, because default dest name is derived from long option
                      type="int",       # "string" is default, other types: "int", "long", "choice", "float" and "complex"
                      action="store",      # "store" is default, other actions: "store_true", "store_false" and "append"
                      #default="8080", # set default value here, None is used otherwise
                      help="port",
                      )
    parser.add_option(
                      "-c", "--clients",    # short and long option
                      dest="max_clients",       # not needed in this case, because default dest name is derived from long option
                      type="int",
                      action="store",      # "store" is default, other actions: "store_true", "store_false" and "append"
                      #default="15", # set default value here, None is used otherwise
                      help="max. number of clients",
                      )
    parser.add_option(
                      "-w", "--welcome",    # short and long option
                      dest="welcome_str",       # not needed in this case, because default dest name is derived from long option
                      type="string",       # "string" is default, other types: "int", "long", "choice", "float" and "complex"
                      action="store",      # "store" is default, other actions: "store_true", "store_false" and "append"
                      #default="Vitejte!", # set default value here, None is used otherwise
                      help="welcome message",
                      )
    options, args = parser.parse_args()
    print(options)
    print(args)
    return((options, args))

def config_file(filenames):   
    config = configparser.SafeConfigParser()
    for filename in filenames:
        config.read(filename)
    return config