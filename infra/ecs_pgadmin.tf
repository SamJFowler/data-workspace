resource "aws_ecs_task_definition" "pgadmin" {
  family                = "${var.prefix}-pgadmin"
  container_definitions = "${data.template_file.pgadmin_container_definitions.rendered}"
  execution_role_arn    = "${aws_iam_role.notebook_task_execution.arn}"
  # task_role_arn         = "${aws_iam_role.notebook_task.arn}"
  network_mode          = "awsvpc"
  cpu                   = "${local.notebook_container_cpu}"
  memory                = "${local.notebook_container_memory}"
  requires_compatibilities = ["FARGATE"]

  volume {
    name = "home_directory"
  }

  lifecycle {
    ignore_changes = [
      "revision",
    ]
  }
}

data "external" "pgadmin_current_tag" {
  program = ["${path.module}/task_definition_tag.sh"]

  query = {
    task_family = "${var.prefix}-pgadmin"
    container_name = "${local.notebook_container_name}"
  }
}

data "external" "pgadmin_metrics_current_tag" {
  program = ["${path.module}/task_definition_tag.sh"]

  query = {
    task_family = "${var.prefix}-pgadmin"
    container_name = "metrics"
  }
}

data "external" "pgadmin_s3sync_current_tag" {
  program = ["${path.module}/task_definition_tag.sh"]

  query = {
    task_family = "${var.prefix}-pgadmin"
    container_name = "s3sync"
  }
}

data "template_file" "pgadmin_container_definitions" {
  template = "${file("${path.module}/ecs_notebooks_notebook_container_definitions.json")}"

  vars {
    container_image  = "${var.pgadmin_container_image}:${data.external.pgadmin_current_tag.result.tag}"
    container_name   = "${local.notebook_container_name}"
    container_cpu    = "${local.notebook_container_cpu}"
    container_memory = "${local.notebook_container_memory}"

    log_group  = "${aws_cloudwatch_log_group.notebook.name}"
    log_region = "${data.aws_region.aws_region.name}"

    sentry_dsn = "${var.sentry_dsn}"
    sentry_environment = "${var.sentry_environment}"

    metrics_container_image = "${var.metrics_container_image}:${data.external.pgadmin_metrics_current_tag.result.tag}"
    s3sync_container_image = "${var.s3sync_container_image}:${data.external.pgadmin_s3sync_current_tag.result.tag}"

    home_directory = "/home/pgadmin"
  }
}
