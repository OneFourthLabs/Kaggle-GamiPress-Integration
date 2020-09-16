from integration.core import Integrator

def main():
    i = Integrator('config.json')
    i.run_rewarder()

if __name__ == '__main__':
    ## Just for Testing
    main()
    # TODO: Replace above with a scheduler
