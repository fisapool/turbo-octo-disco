output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.hr_analytics_vpc.id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "ecs_cluster_name" {
  description = "The name of the ECS cluster"
  value       = aws_ecs_cluster.hr_analytics_cluster.name
}

output "ecs_service_name" {
  description = "The name of the ECS service"
  value       = aws_ecs_service.hr_analytics_service.name
}

output "load_balancer_dns" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.hr_analytics_lb.dns_name
}

output "load_balancer_zone_id" {
  description = "The zone ID of the load balancer"
  value       = aws_lb.hr_analytics_lb.zone_id
}

output "grafana_endpoint" {
  description = "The endpoint for Grafana"
  value       = "http://${aws_lb.hr_analytics_lb.dns_name}:3000"
}

output "prometheus_endpoint" {
  description = "The endpoint for Prometheus"
  value       = "http://${aws_lb.hr_analytics_lb.dns_name}:9090"
}

output "app_endpoint" {
  description = "The endpoint for the application"
  value       = "http://${aws_lb.hr_analytics_lb.dns_name}"
}

output "ecs_task_execution_role_arn" {
  description = "The ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution_role.arn
}

output "ecs_task_role_arn" {
  description = "The ARN of the ECS task role"
  value       = aws_iam_role.hr_analytics_task_role.arn
} 