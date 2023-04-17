from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    Stage,
    Environment,
    pipelines,
    aws_codepipeline as codepipeline
)
from constructs import Construct
from resource_stack.resource_stack import ResourceStack


class DeployStage(Stage):
    def __init__(self, scope: Construct, id: str, env: Environment, **kwargs) -> None:
        super().__init__(scope, id, env=env, **kwargs)
        ResourceStack(self, 'ResourceStack', env=env, stack_name="resource-stack-deploy")


class AwsCodepipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # pulls code from github repo
        git_input = pipelines.CodePipelineSource.connection(
            repo_string="pasrichashivam/aws_codepipeline",
            branch="main",
            connection_arn="arn:aws:codestar-connections:ap-south-1:622664665083:connection/53e58df8-b085-4424-890f-5d488817df34"
        )

        # After pulling the code create code pipeline
        code_pipeline = codepipeline.Pipeline(
            self, "Pipeline",
            pipeline_name="new-pipeline",
            cross_account_keys=False  # in
        )

        synth_step = pipelines.ShellStep(
            id="Synth",
            install_commands=[
                'pip install -r requirements.txt'
            ],
            commands=[
                'npx cdk synth'
            ],
            input=git_input
        )

        pipeline = pipelines.CodePipeline(
            self, 'CodePipeline',
            self_mutation=True,
            code_pipeline=code_pipeline,
            synth=synth_step
        )

        deployment_wave = pipeline.add_wave("DeploymentWave")

        deployment_wave.add_stage(DeployStage(
            self, 'DeployStage',
            env=(Environment(account='622664665083', region='ap-south-1'))
        ))
