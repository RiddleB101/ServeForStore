;
var upload = {
    error: function (msg) {
        common_ops.alert(msg);
    },
    success: function (file_key) {
        if (!file_key) {
            return;
        }
        var html = '<img src="' + common_ops.buildPicUrl(file_key) + '"/>' + '<span class="fa fa-times-circle del del_image" data="' + file_key + '"></span>';

        if ($(".upload_pic_wrap .pic-each").size() > 0) {
            $(".upload_pic_wrap .pic-each").html(html);
        } else {
            $(".upload_pic_wrap").append('<span class="pic-each">' + html + '</span>');
        }
        product_set_ops.deleteImg();
    }
};

var product_set_ops = {
    init: function () {
        this.eventBind();
        this.deleteImg();
    },
    eventBind: function () {
        $(".wrap_product_set .upload_pic_wrap input[name=pic]").change(function () {
            $(".wrap_product_set .upload_pic_wrap").submit();
        });

        $(".wrap_product_set input[name=tags]").tagsInput({
            width: 'auto',
            height: 40
        });

        $(".wrap_product_set .save").click(function () {
            var btn_target = $(this);
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在处理!!请不要重复提交~~");
                return;
            }

            var cat_id_target = $(".wrap_product_set select[name=cat_id]");
            var cat_id = cat_id_target.val();

            var name_target = $(".wrap_product_set input[name=name]");
            var name = name_target.val();

            var price_target = $(".wrap_product_set input[name=price]");
            var price = price_target.val();

            var summary = $.trim(that.ue.getContent());

            var stock_target = $(".wrap_product_set input[name=stock]");
            var stock = stock_target.val();

            var tags_target = $(".wrap_product_set input[name=tags]");
            var tags = $.trim(tags_target.val());

            if (parseInt(cat_id) < 1) {
                common_ops.tip("请选择分类~~", cat_id_target);
                return;
            }

            if (name.length < 1) {
                common_ops.alert("请输入符合规范的名称~~");
                return;
            }

            if (parseFloat(price) <= 0) {
                common_ops.tip("请输入符合规范的售卖价格~~", price_target);
                return;
            }

            if ($(".wrap_product_set .pic-each").size() < 1) {
                common_ops.alert("请上传封面图~~");
                return;
            }

            if (summary.length < 10) {
                common_ops.tip("请输入描述，并不能少于10个字符~~", price_target);
                return;
            }

            if (parseInt(stock) < 1) {
                common_ops.tip("请输入符合规范的库存量~~", stock_target);
                return;
            }

            if (tags.length < 1) {
                common_ops.alert("请输入标签，便于搜索~~");
                return;
            }

            btn_target.addClass("disabled");

            var data = {
                cat_id: cat_id,
                name: name,
                price: price,
                main_image: $(".wrap_product_set .pic-each .del_image").attr("data"),
                summary: summary,
                stock: stock,
                tags: tags,
                id: $(".wrap_product_set input[name=id]").val()
            };

            $.ajax({
                url: common_ops.buildUrl("/food/set"),
                type: 'POST',
                data: data,
                dataType: 'json',
                success: function (res) {
                    btn_target.removeClass("disabled");
                    var callback = null;
                    if (res.code == 200) {
                        callback = function () {
                            window.location.href = common_ops.buildUrl("/food/index");
                        }
                    }
                    common_ops.alert(res.msg, callback);
                }
            });
        })
    },
    deleteImg: function () {
        $(".upload_pic_wrap .del_image").unbind().click(function () {
            $(this).parent().remove();
        })
    }
};

$(document).ready(function () {
    product_set_ops.init();
});