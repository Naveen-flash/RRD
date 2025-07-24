module "eks" {
  source             = "./modules/eks"
  cluster_name       = "EKS-Cluster"
  vpc_id             = "vpc-0339bd5c9bbbc717e"
  private_subnet_ids = ["subnet-086b1c854380f67e2", "subnet-062cb390cb1b318f6"]
  region             = "ap-south-1"
  node_instance_type = "t3.medium"
  desired_capacity   = 2

  coredns_version    = "v1.12.1-eksbuild.2"
  kube_proxy_version = "v1.33.0-eksbuild.2"
  vpc_cni_version    = "v1.19.5-eksbuild.1"
}
