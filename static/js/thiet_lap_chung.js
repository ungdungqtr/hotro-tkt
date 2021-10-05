$(document).ready(function () {
    $(document).find('.save_btn').hide();
    $(document).find('.cancel_btn').hide(); 
    $('.cap_nhat_qd').click(function (e) { 
        e.preventDefault();
        var id = $(this).attr('value');
        if (id) {
            tr_id = '#qd-' + id;
            so_qd = $(tr_id).find('.QDso').text();
            ten_qd = $(tr_id).find('.QDten').text();
            ngay_qd = $(tr_id).find('.QDngay').text();
            date_str = ngay_qd.split('/');
            $('#qd-id').val(id);
            $('#qd-so').val(so_qd);
            $('#qd-ten').val(ten_qd);
            $('#qd-ngay').val(date_str[2]+'-'+date_str[1]+'-'+date_str[0]);
        }       
    });

    $('#modal_qd_form').submit(function () { 
        // e.preventDefault();
        var idInput = $('#qd-id').val();
        var SoInput = $('#qd-so').val().trim();
        var TenInput = $('#qd-ten').val().trim();
        var NgayInput = $('#qd-ngay').val();
        
        if (SoInput && TenInput && NgayInput) {
            $.ajax({
                url: "cap_nhat_qd",
                data: {
                    'id': idInput,
                    'so_qd': SoInput,
                    'ten_qd': TenInput,
                    'ngay_qd': NgayInput,
                },
                dataType: "json",
                success: function (data) {
                    if (data.qd) {
                        UpdateQDTable(data.qd);
                    }
                }
            });
        }       
        $('form#modal_qd_form').trigger("reset");
        $('#UpdateQD').modal('hide');
        return false;
    });

    function UpdateQDTable(qd) {
        $("#can_cu #qd-" + qd.id).children(".QdData").each(function() {
            var attr = $(this).attr("name");
            if (attr == "QDso") {
              $(this).text(qd.so_qd);
            } else if (attr == "QDten") {
              $(this).text(qd.ten_qd);
            } else {
              $(this).text(qd.ngay_qd);
            }
        });
    }

    $('.edit_btn').each( function () {
        $(this).click(function (e){
            e.preventDefault();
            var ld = $(this).closest('tr');
            var ld_ten = ld.find('#ld_ten');
            
            ld_ten.attr('contenteditable', 'true');
            ld_ten.css("background-color", "#FFC107");
            ld.find('.save_btn').show();
            ld.find('.cancel_btn').show();
            $(this).hide();
            ld_ten.attr('original_entry', ld_ten.html());
            $(ld_ten).autocomplete({
                minLength: 2,
                source : 'cb_ten_autocomplete',
            });
        });
    });

    $('.save_btn').each( function () {
        $(this).click(function (e) { 
            e.preventDefault();
            var ld = $(this).closest('tr');
            var ld_ten = ld.find('#ld_ten');
            var ten_cb = ld_ten.text();
            var id = ld.attr('id').substring(3);
            $.ajax({
                url: "cap_nhat_ld",
                data: {'ld_ten': ten_cb, 'id': id},
                dataType: "json",
                success: function (data) {
                    if (data.ld) {
                        updateToLDTabel(data.ld);                       
                        ld_ten.attr('contenteditable', 'false');   
                        ld_ten.css("background-color", "white");                     
                    } else {
                        alert("Cán bộ không có tên trong danh sách\nVui lòng cập nhật");
                        ld_ten.text('');   
                    }
                }
            });
            $(this).hide();
            ld.find('.cancel_btn').hide();
            ld.find('.edit_btn').show();
        });
    });
    
    $('.cancel_btn').each(function () {
        $(this).click(function (e) { 
            e.preventDefault();
            var ld = $(this).closest('tr');
            var ld_ten = ld.find('#ld_ten');
            ld_ten.html(ld_ten.attr('original_entry') ); 
            $(this).hide();
            ld.find('.save_btn').hide();
            ld.find('.edit_btn').show();
            ld_ten.attr('contenteditable', 'false');   
            ld_ten.css("background-color", "white"); 
        });
    });

    function updateToLDTabel(ld) {
        $("#LDTable #ld-" + ld.id).children(".LdData").each(function() {
            var attr = $(this).attr("name");
            if (attr == "LDgt") {
                $(this).text(ld.ld_gt);
            } else if (attr == "LDten") {
                $(this).text(ld.ld_ten);
            } else {
                $(this).text(ld.ld_cv);
            }
          });
    }
});
