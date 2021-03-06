"""
Copyright (c) 2015 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the BSD license. See the LICENSE file for details.
"""

from atomic_reactor.plugin import PostBuildPlugin


__all__ = ('TagByLabelsPlugin', )


class TagByLabelsPlugin(PostBuildPlugin):
    """
    Use labels name, version and release of final image and create tags:
     * name:version
     * name:version-release
    """
    key = "tag_by_labels"
    is_allowed_to_fail = False

    def __init__(self, tasker, workflow, **kwargs):
        """
        constructor

        :param tasker: DockerTasker instance
        :param workflow: DockerBuildWorkflow instance
        """
        # call parent constructor
        super(TagByLabelsPlugin, self).__init__(tasker, workflow)
        if kwargs:
            self.log.warning("ignoring arguments %s", kwargs)

    def run(self):
        if not self.workflow.built_image_inspect:
            raise RuntimeError("There are no inspect data of built image. "
                               "Have the build succeeded?")
        if "Labels" not in self.workflow.built_image_inspect["ContainerConfig"]:
            raise RuntimeError("No labels specified.")

        def get_label(label_name):
            try:
                return self.workflow.built_image_inspect["ContainerConfig"]["Labels"][label_name]
            except KeyError:
                raise RuntimeError("Missing label '%s'." % label_name)

        name = get_label("name")
        version = get_label("version")
        release = get_label("release")

        unique_tag = self.workflow.builder.image.tag

        nvr = "%s:%s-%s" % (name, version, release)
        nv = "%s:%s" % (name, version)
        n = "%s:latest" % name
        n_unique = "%s:%s" % (name, unique_tag)

        self.workflow.tag_conf.add_primary_images([nvr, nv, n])
        self.workflow.tag_conf.add_unique_image(n_unique)
