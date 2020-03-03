def watch_param_across_instances(origin, origin_param, target, target_param):
    """
    Have value of target_param on instance param update to value origin_param on instance param.
    """
    def callback(*events):
        for event in events:
            setattr(target, target_param, event.new)

    watcher = origin.param.watch(callback, [origin_param], onlychanged=False)
    origin.param.trigger(origin_param)
    return watcher
