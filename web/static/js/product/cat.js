;
var product_cat_ops = {
    init: function () {
        this.eventBind();
    },
    eventBind: function () {
        var that = this;
        // 通过判断选择框是否发生变化调用回调函数
        $(".wrap_search select[name=status]").change(function () {
            $(".wrap_search .search").submit()
        });

        $(".remove").click(function () {
            that.ops('remove', $(this).attr("data"));
        });

        $(".recovery").click(function () {
            that.ops('recovery', $(this).attr("data"));
        });
    },
    ops: function (action, id) {
        var callback = {
            'ok': function () {
                $.ajax({
                    url: common_ops.buildUrl("/product/ops"),
                    type: "POST",
                    data: {
                        action: action,
                        id: id
                    },
                    dataType: "json",
                    success: function (res) {
                        var callback = null;
                        if (res.code === 200) {
                            callback = function () {
                                window.location.href = window.location.href;
                            }
                        }
                        common_ops.alert(res.msg, callback)
                    }
                })
            },
            'cancel': null
        };
        common_ops.confirm((action == "remove" ? "确定删除吗？" : "确定恢复吗？"), callback)

    }
};

$(document).ready(function () {
    product_cat_ops.init()
});