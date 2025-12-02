#!/usr/bin/env python3
import aws_cdk as cdk

from compData_product_consumer.compData_product_consumer import CompDataProductConsumerStack


app = cdk.App()
env = app.node.try_get_context("env")
aws_account = app.node.try_get_context(env)["account"]

aws_env = cdk.Environment(account=aws_account, region=app.node.try_get_context(env)["region"])
CompDataProductConsumerStack(app, "esi-compData-product-consumer", env=aws_env)
app.synth()