# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.

from aws_cdk import (
    Stack
)

# from cdk_nag import (AwsSolutionsChecks, NagSuppressions)
# from cdkstandard.cdkintegration import IntegrationBase
from constructs import Construct
from signet_cdk_common_constructs import ESIIntegrationBase

class CompDataProductConsumerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        esiBase =  ESIIntegrationBase(self, 'esi-compData-product-consumer' )
        lambdaFn = esiBase.create_cloud_map_lambda("lambdaConfig")