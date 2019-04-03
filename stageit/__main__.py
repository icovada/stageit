from device import device
import yaml



if __name__ == '__main__':
    config = yaml.load('term_config.yaml')

    d = device("192.168.0.1", 2033, 'telnet', 'ios', 'cisco', 'cisco')