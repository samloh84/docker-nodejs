def render_template_list(template_list, render_data, environment):
    def render_template_string(template_string):
        template = environment.from_string(template_string)
        return template.render(render_data)

    return map(render_template_string, template_list)
