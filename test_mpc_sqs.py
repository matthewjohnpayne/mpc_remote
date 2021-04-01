import mpc_sqs
import time
import string
import random

# sample dict to be submitted
sample_dict = { 'trackletID': ''.join([ random.choice(string.ascii_uppercase+string.ascii_lowercase) for _ in range(10) ]),
                'desig12': '2002 AB1',
                'mpc_local_queue_destination': 'MBAMOPP'}

# instantiate
OES = mpc_sqs.OrbfitExtensionSQS()

# send
print('Sending...\n',sample_dict)
OES.send( sample_dict , OES._sample_message_body_string() )

'''

# wait
n_sec =10
print(f'Sleeping for {n_sec} seconds')
time.sleep(n_sec)

# read
print('Reading...')
job_dict = OES.read()
print('job_dict=',job_dict)

if job_dict:

    # wait
    n_sec =10
    print(f'Sleeping for {n_sec} seconds')
    time.sleep(n_sec)

    # delete
    ### # calculate ( *not* part of the OES class)
    ### result_dict = do_orbit_fit(job_dict)
    # update queue by deleting job
    ### >>> if result_dict['successful'] : OES.delete()
    print('Deleting...')
    OES.delete()

'''
