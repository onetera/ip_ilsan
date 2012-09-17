import logging

#logging.warning("watch out")
#logging.info("ok with that")


#logging.basicConfig(filename='/home/d10218/example.log',level=logging.DEBUG)
#logging.debug('This message should go to the log file')
#logging.info('So should this')
#logging.warning('And this, too')

#logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
#logging.warn("Hello")
#logging.error("Still here...")
#logging.warn("Goodbye")



logging.basicConfig(level=logging.DEBUG)

def m():
    1/0

def n():
    logging.debug("Inside f!")
    try:
        m()
    except Exception, ex:
        logging.exception("Something awful happened!")
    logging.debug("Finishing f!")


n()    
    
    
    
def g():
    1 / 0

def f():
    print "inside f!"
    try:
        g()
    except Exception, ex:
        print "Something awful happened!"
    print "Finishing f!"

f()


