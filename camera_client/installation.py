import os
import time



def buildTemporaryStore():
    try:
        if not os.path.isdir('./bin/store'):
            os.mkdir('./bin/store')

    except Exception as e:
        print(f'Failed to create TemporaryImageStore because: {e}')
        time.sleep(5)


if __name__ == '__main__':
    print('Building Temporary Image Store')
    buildImageStore()