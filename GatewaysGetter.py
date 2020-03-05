import json
import argparse
import boto3

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
        help="REST method(s) filter if not specified that means ALL",
    )
    return parser


if __name__ == "__main__":
    args_parser = create_args_parser()
    args = args_parser.parse_args()
    print(args)
    session = boto3.Session(profile_name=args.profile)
    client = session.client("apigateway", region_name=args.region)
    apis = client.get_rest_apis()["items"]
    for api in apis:
        resources = client.get_resources(restApiId=api["id"])["items"]
        print(json.dumps(api, indent=4, default=str))
        for index, resource in enumerate(resources):
            for method in resource["resourceMethods"].keys():
                if "ALL" in args.methods or method in args.methods:
                    methodInfo = client.get_method(
                        restApiId=api["id"],
                        resourceId=resource["id"],
                        httpMethod=method,
                    )
                    del methodInfo["ResponseMetadata"]
                    resource["resourceMethods"][method] = methodInfo
            print(index, json.dumps(resource, indent=4, default=str))
