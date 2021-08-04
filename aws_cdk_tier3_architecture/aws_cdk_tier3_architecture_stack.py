from aws_cdk import (
aws_ec2 as ec2,
core as cdk,
aws_s3 as s3,
aws_elasticloadbalancing as elb,
aws_elasticloadbalancingv2 as elba,
aws_autoscaling as autoscaling,
aws_rds as rds
)
from aws_cdk_tier3_architecture.myvars import *

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core


class AwsCdkTier3ArchitectureStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        
        #workload VPC custom
        workload_vpc = ec2.Vpc(self, 'default_vpc', cidr=VPC_CIDR)
        
        #webserver security group
        webserver_sg = ec2.SecurityGroup(self, id='sg', vpc=workload_vpc, security_group_name=WEBSERVER_SG,
        description=DES_SG)
        #inbound rules   
        webserver_sg.add_ingress_rule(peer=ec2.Peer.ipv4(ING_PEER_RANGE), connection=ec2.Port.tcp(ING_SSH_PORT))
        webserver_sg.add_ingress_rule(peer=ec2.Peer.ipv4(ING_PEER_RANGE), connection=ec2.Port.tcp(ING_HTTP_PORT))
        webserver_sg.add_ingress_rule(peer=ec2.Peer.ipv4(ING_PEER_RANGE), connection=ec2.Port.tcp(ING_HTTPS_PORT))
        #security group id in varibale
        webserver_sg_id = cdk.CfnOutput(self, "sg_id", value=webserver_sg.security_group_id)

        #Autoscaling Launch Configuration
        asc= autoscaling.CfnLaunchConfiguration(
            self, id="ASC", 
            launch_configuration_name = AS_LC_NAME,
            image_id = AMI,
            instance_type = INS_TYPE,
            associate_public_ip_address = True,
            key_name = EC2_KEY,
            security_groups= [WEBSERVER_SG],
            #user_data = ("yum install -y nginx")
         )


        #Autoscaling Group 
        asg = autoscaling.CfnAutoScalingGroup(
            self, id="ASG",
            auto_scaling_group_name = ASG_NAME,
            max_size = MIN_ASG,
            min_size = MAX_ASG,
            desired_capacity = DES_CAP,
            availability_zones =["us-east-1a","us-east-1b"],
            launch_configuration_name = AS_LC_NAME
            #load_balancer_names = elbclassic

        )

        #Classic ELB 
        elbc= elb.LoadBalancer(
            self, id="classicsample",
            vpc= workload_vpc, 
            cross_zone = True,
            internet_facing = True
            
        )
        elbc.add_listener(external_port=ING_HTTP_PORT, internal_port=ING_HTTP_PORT)
        #elbc.add_target(target=elb.ILoadBalancerTarget(asg))



        # #ELB for above two insntances 
        # elbclassic= elb.LoadBalancer(self, "classicelb", vpc=workload_vpc, internet_facing=True, health_check={"port": 80})
        # #adding target to elb
        # elbclassic.add_target(asg)
        # listener = elbclassic.add_listener(external_port=ING_HTTP_PORT)
        # listener.connections.allow_default_port_from_any_ipv4("Open to the world")


        # asg = autoscaling.AutoScalingGroup(
        #     self, "ASG",
        #     vpc=workload_vpc,
        #     instance_type=ec2.InstanceType.of(
        #         ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
        #     ),
        #     machine_image=ec2.AmazonLinuxImage(),
        # )


