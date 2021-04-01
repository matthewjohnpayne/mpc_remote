'''
MJP 2021-03-30
Getting started with AWS SQS

(1) AWS Documentation
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-sending-receiving-msgs.html

(2) You need to set-up configuration: I used AWS CLI
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html



'''

# Third party imports
import boto3
from datetime import datetime
import os
import logging
import functools

# Create SQS client
sqs = boto3.client('sqs')


# -------- Logging & Error-Handling --------------------------------------
def _generate_log(func_type, log_type):
    """
    Create a logger object
    """
    assert log_type in ['ERROR' , 'INFO']
    loggerName  = func_type + "_" + log_type
    logFile     = f'{loggerName}.log'
    
    # Create a logger and set the level.
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.ERROR if log_type == 'ERROR' else logging.INFO )

    # Create file handler, log format and add the format to file handler
    file_handler = logging.FileHandler( logFile )

    # See https://docs.python.org/3/library/logging.html#logrecord-attributes
    # for log format attributes.
    formatter = logging.Formatter( '%(levelname)s %(asctime)s %(message)s' )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logging.getLogger(loggerName)



def log_success(func_type, result):
    ''' What we want to log for the various functions '''
    assert func_type in ['send','read','delete']
    logger = _generate_log(func_type, 'INFO')
    if   func_type == 'send':
        msg = 'Sent: %s' % result
    elif func_type == 'read':
        msg = 'Read: %r' % result if result else 'No Jobs'
    elif func_type == 'delete':
        msg = 'Deleted: %r' % result
    else:
        assert False

    logger.info(msg)
    logger.handlers.clear()
    del logger

def log_failure(func_type, err):
    assert func_type in ['send','read','delete']
    logger = _generate_log(func_type, 'ERROR')
    logger.exception(f'\nError in {func_type}\n')
    logger.handlers.clear()
    del logger

def log_with_err( func_type = None ):
    '''
    NB: We create a parent function to take arguments
    ...
    '''
    
    def error_log(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            try:
                # Execute the called function & log success
                result = func(*args, **kwargs)
                log_success(func_type, result)
                return result
                
            except Exception as e:
                # Log failure
                log_failure(func_type, e )
                return False

        return wrapper

    return error_log












# -------- SQS Classes --------------------------------------

class MPCSQS():
    '''
    Setting up a class to send/receive/delete messages from MPC queue(s) on AWS SQS
    
    This class should *NOT* be used directly ...
     - See child classes below for desired explicit calls
    '''
    
    def __init__(self, queue_url):
        self.queue_url = queue_url
        
        # Variables used to read from queue
        self.job_dict               = None
        self.receipt_handle         = None

    # ----- send to queue ---------------------------------
    @log_with_err(func_type = 'send')
    def send(self, job_dict , message_body_string):
        '''
            Send message to SQS queue
            Decorator logs & catches errors
        '''
        # convert simple message dict to aws-format
        aws_dict = self.transform_standard_dict_to_aws_dict(job_dict)
        
        # send message
        response = sqs.send_message(
            QueueUrl=self.queue_url,
            DelaySeconds=1,
            MessageAttributes= aws_dict,
            MessageBody=(message_body_string)
        )
        
        return response['MessageId']

    # ----- read from queue -------------------------------
    @log_with_err(func_type = 'read')
    def read(self,):
        '''
            Read/parse a fetched job
            Decorator logs & catches errors
        '''
        
        # Fetch the next job from the queue
        queue_response = self._fetch()
        
        # Check job message is correctly formatted
        self.job_dict = self._parse_queue_response(queue_response)
        
        return self.job_dict

    def _fetch(self,):
        ''' Fetch a single message from an SQS queue '''
        return sqs.receive_message(
            QueueUrl=self.queue_url,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )


    def _parse_queue_response(self,queue_response):
        ''' parse a fetched job-message to create a standard job-dictionary '''
        
        if 'Messages' not in queue_response:
            # No jobs in queue
            job_dict = {}
        else:
            message             = queue_response['Messages'][0]
            self.receipt_handle = message['ReceiptHandle']

            aws_dict = message['MessageAttributes']
            job_dict = self.transform_aws_dict_to_standard_dict(aws_dict)
            
        return job_dict
        
    # ----- delete from queue -------------------------------
    @log_with_err(func_type = 'delete')
    def delete(self, ):
        '''
            Delete received message from queue
            Decorator logs & catches errors
        '''
        return sqs.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=self.receipt_handle
        )['ResponseMetadata']['RequestId']

    # ----- sample dictionaries -----------------------------
    def _sample_message_attributes_dict(self,):
        ''' This is ONLY FOR TESTING '''
        return {
                    'test_attribute': {
                        'DataType': 'String',
                        'StringValue': 'kjhadbfhadbfljahdsbflajhbsf'
                    },
                }
                
    def _sample_message_body_string(self,):
        ''' This is ONLY FOR TESTING '''
        return 'MPCSQS: Sent: ' + self._now_str()

    def _now_str(self,):
        return datetime.now().strftime("%m/%d/%Y_%H:%M:%S")
    
    # ----- transform dictionaries ---------------------------
    def transform_standard_dict_to_aws_dict(self, in_d):
        ''' '''
        # Check the input dict has the required attributes
        for k in self._sample_message_attributes_dict():
            assert k in in_d
            
        # Get the default aws dict
        aws_d = self._sample_message_attributes_dict()
        
        # Change the content of the aws-dict to match the input
        for k in self._sample_message_attributes_dict():
            aws_d[k]['StringValue'] = in_d[k]

        return aws_d
        
    def transform_aws_dict_to_standard_dict(self , aws_d):
        ''' ... '''
        for key in self._sample_message_attributes_dict():
            assert key in aws_d

        return {key: aws_d[key]['StringValue'] for key in self._sample_message_attributes_dict() }

class OrbfitExtensionSQS(MPCSQS):
    '''
    
    E.g.
    >>> # instantiate
    >>> OES = OrbfitExtensionSQS()
    >>> # send
    >>> OES.send( message_attributes_dict , message_body_string)
    >>> # read
    >>> job_dict = OES.read()
    >>> # calculate ( *not* part of the OES class)
    >>> result_dict = do_orbit_fit(job_dict)
    >>> # update queue
    >>> if result_dict['successful'] : OES.delete()
    '''
    
    def __init__(self,):
        MPCSQS.__init__(self,  'https://sqs.us-east-1.amazonaws.com/071807599513/mpc_orbfit_extension_general')
            
    def _sample_message_attributes_dict(self,):
        '''  '''
        return {
                    'trackletID': {
                        'DataType': 'String',
                        'StringValue': 'hvgkvvgvuuvuvuvfu'
                    },
                    #'suggested_unpacked_primary_provisional_designation': {
                    #    'DataType': 'String',
                    #    'StringValue': '2002 AB1'
                    #},
                    'desig12': {
                        'DataType': 'String',
                        'StringValue': '     KBA00B'
                    },
                    'mpc_local_queue_destination': {
                        'DataType': 'String',
                        'StringValue': 'MBAMOPP'
                    }
                }
                
    def _sample_message_body_string(self,):
        '''  '''
        return 'OrbfitExtensionSQS: Sent: ' + self._now_str()
        
        

def auto_ack_batch_send_to_sqs_queue( obs_to_tracklet_with_dest_dict):
    """
    This takes a hacked-together dictionary from "separatesubmission.py" (in autoack)
    The dict looks like
        key = obs80_bit
        val = ( mpc_local_queue_destination , trackletID , desig12 )
    This is *NOT* intended to be the final version of this function:
     - I am just hacking together something to do an initial send to an AWS SQS queue
     - Eventually we will want to send to different sqs queus depending on destination_directory + desig12
    """
    # Instantiate OrbfitExtensionSQS
    OES = OrbfitExtensionSQS()
    
    # Loop through the "batch dictionary" from autoack
    for obs80_bit, _ in obs_to_tracklet_with_dest_dict.items():
        # Extract the data from the tuple in the dict-value field
        mpc_local_queue_destination , trackletID , desig12 = _
        
        # Group by trackletID
        if trackletID not in tracklet_dict.items():
            tracklet_dict[trackletID] = {   'mpc_local_queue_destination'   : [mpc_local_queue_destination],
                                            'desig12'                       : [desig12]}
        else:
            tracklet_dict[trackletID]['mpc_local_queue_destination'].append(mpc_local_queue_destination)
            tracklet_dict[trackletID]['desig12'].append(desig12)
        
    # make dict suitable for sending to aws queue
    for trackletID, _ in tracklet_dict.items():
    
        # Check that the destination & designation are unique
        assert len(set( _['mpc_local_queue_destination'] )) == 1
        assert len(set( _['desig12'] )) == 1
        
        # make simple dictionary
        standard_dict = {   'trackletID'                    : trackletID ,
                            'desig12'                       : _['desig12'][0],
                            'mpc_local_queue_destination'   : _['mpc_local_queue_destination'][0]
                        }
        
        # send to queue
        print('Sending...\n',sample_dict)
        OES.send( sample_dict , OES._sample_message_body_string() )
