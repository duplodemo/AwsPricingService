# AwsPricingService
Service that serves AWS instance pricing

To run this outside the docker container, make sure u have the right python packages
python pricingsvc.py &

Example usage
curl -X POST -H "Content-Type: application/json" -d '{"location":"US West (Oregon)","instanceType":"t2.2xlarge", "operatingSystem":"Windows"}'  http://127.0.0.1/api/v1.0/findOnDemandHourlyPrice

