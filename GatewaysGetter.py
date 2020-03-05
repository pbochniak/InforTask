import json
import argparse

import boto3
from botocore.exceptions import BotoCoreError

REST_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
FORMATS = ["json", "json-pretty", "csv"]


def create_args_parser():
    parser = argparse.ArgumentParser(description="AWS API Gateways information getter.")
    parser.add_argument(
        "-r", "--region", required=True, metavar="REGION_NAME", help="Gateway region",
    )
    parser.add_argument(
        "-p",
        "--profile",
        default="default",
        metavar="PROFILE_NAME",
        help="Credentials profile",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="json",
        metavar="FORMAT",
        choices=FORMATS,
        help="Output format",
    )
    parser.add_argument(
        "-m",
        "--methods",
        default=["ALL"],
        nargs="+",
        metavar="REST_METHOD",
        choices=REST_METHODS,
        help="REST method(s) filter if not specified that means ALL",
    )
    return parser


class Getter:
    def __init__(self, config):
        self.__config = config
        self.__client = boto3.Session(
            profile_name=self.__config.profile, region_name=self.__config.region
        ).client("apigateway")
        self.__apis = {}

    def load(self):
        for api in self.__client.get_rest_apis()["items"]:
            self.load_resources(api)
            self.__apis[api["name"]] = api

    def load_resources(self, api):
        endpoints = {}
        for resource in self.__client.get_resources(restApiId=api["id"])["items"]:
            self.load_methods(api, resource)
            endpoints[resource["path"]] = resource
        api["endpoints"] = endpoints

    def load_methods(self, api, resource):
        methods = resource["resourceMethods"]
        for method in methods.keys():
            if (
                method not in self.__config.methods
                and "ALL" not in self.__config.methods
            ):
                continue
            methodInfo = self.__client.get_method(
                restApiId=api["id"], resourceId=resource["id"], httpMethod=method
            )
            del methodInfo["ResponseMetadata"]
            methods[method] = methodInfo

    def output(self):
        if self.__config.format == "json":
            return json.dumps(self.__apis, default=str)
        if self.__config.format == "json-pretty":
            return json.dumps(self.__apis, indent=4, default=str)
        if self.__config.format == "csv":
            raise NotImplementedError("CSV format TODO")


if __name__ == "__main__":
    args_parser = create_args_parser()
    try:
        getter = Getter(args_parser.parse_args())
        getter.load()
        print(getter.output())
    except BotoCoreError as ex:
        print(f"ERROR: {str(ex)}")
