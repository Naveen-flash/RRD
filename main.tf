module "eks" {
  source             = "./modules/eks"
  cluster_name       = "my-private-eks"
  vpc_id             = "vpc-07fd7d5200ed8fa32"
  private_subnet_ids = ["subnet-05bc487e3e432df34", "subnet-0d7a4f487d3e685c8"]
  region             = "us-east-1"
  node_instance_type = "t2.micro"
  desired_capacity   = 2

  coredns_version    = "v1.11.1-eksbuild.4"
  kube_proxy_version = "v1.29.0-eksbuild.1"
  vpc_cni_version    = "v1.14.1-eksbuild.1"
}