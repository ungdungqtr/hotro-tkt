$(document).ready(function () {
    $(function() {
        $("input[name='mst']").on('input', function(e) {
            $(this).val($(this).val().replace(/[^0-9|-]/g, ''));
        });
    });

    $("input[name='mst']").change(function (e) { 
        e.preventDefault();
        mst = $(this).val();
        regex_1 = /\d{10}/g;
        regex_2 = /\d{10}-\d{3}/g;
        if ((mst.length == 10 && regex_1.test(mst)) || 
            (mst.length == 14 && regex_2.test(mst))) {

        } else {
            alert("Mã số thuế không hợp lệ");
            $(this).val('');
        }
    });
    
    $('form#them_nnt').submit(function () { 
        // e.preventDefault();
        var mstInput = $('input[name="mst"]').val().trim();
        var tenInput = $('input[name="ten_nnt"]').val().trim();
        var dchiInput = $('input[name="dia_chi"]').val().trim();
        var cqtInput = $('select[name="cqt"]').val().trim();

       
        if (mstInput && tenInput && dchiInput && cqtInput) {
            $.ajax({
                url: "them_moi_nnt",
                data: {
                    'mst' : mstInput,
                    'ten_nnt' : tenInput,
                    'dia_chi' : dchiInput,
                    'cqt' : cqtInput
                },
                dataType: "json",
                success: function (data) {
                    if (data.nnt) {
                        appendToUsrTable(data.nnt);
                    }
                }
            });
        } else {
            alert("Yêu cầu điền đầy đủ thông tin NNT");
        }
        $('form#them_nnt').trigger('reset');
    });

    function appendToUsrTable(nnt) {
        $("#userTable > tbody:last-child").append(`
            <tr id="nnt-${nnt.id}">
                <td class="mst userData" name="mst">${nnt.mst}</td>
                <td class="ten_nnt userData" name="ten_nnt">${nnt.ten_nnt}</td>
                <td class="dia_chi userData" name="dia_chi">${nnt.dia_chi}</td>
                <td class="cqt userData" name="cqt">${nnt.cqt}</td>
                <td>
                    <button type="button" class="btn btn-success btn-sm form-control update_nnt" value="${nnt.id}" 
                            data-toggle="modal" data-target="#UpdateModal">
                        <i class="bi bi-pencil-fill"></i>
                    </button>
                </td>
                <td>
                    <button class="btn btn-danger btn-sm form-control xoa_nnt" value="${nnt.id}">
                        <i class="bi bi-trash-fill"></i>
                    </button>
                </td>
            </tr>
        `);
    }

    $('.xoa_nnt').click(function (e) { 
        e.preventDefault();
        var id = $(this).attr('value');
        var action = confirm("Bạn chắc chắc muốn xóa thông tin NNT này?");
        if (action != false) {
            $.ajax({
                url: "xoa_nnt",
                data: {'id' : id},
                dataType: "json",
                success: function (data) {
                    if (data.delete) {
                        $("#userTable #nnt-" + id).remove();
                    }
                }
            });
        }
    });

    $('.update_nnt').click(function (e) { 
        e.preventDefault();
        var id = $(this).attr('value');
        if (id) {
            tr_id = '#nnt-' + id;
            mst = $(tr_id).find('.mst').text();
            ten_nnt = $(tr_id).find('.ten_nnt').text();
            dia_chi = $(tr_id).find('.dia_chi').text();
            cqt = $(tr_id).find('.cqt').text();
            $('#form-id').val(id);
            $('#form-mst').val(mst);
            $('#form-ten').val(ten_nnt);
            $('#form-dchi').val(dia_chi);
            $('#form-cqt').val(cqt);
        }
    });

    $('#UpdateNNT').submit(function () { 
        // e.preventDefault();
        var idInput = $('input[name="formId"]').val().trim();
        var tenInput = $('input[name="formTen"]').val().trim();
        var dchiInput = $('input[name="formDchi"]').val().trim();
        var cqtInput = $('select[name="formCqt"]').val().trim();
        if (tenInput && dchiInput && cqtInput) {
            $.ajax({
                url: "cap_nhat_nnt",
                data: {
                    'id': idInput,
                    'ten_nnt': tenInput,
                    'dia_chi': dchiInput,
                    'cqt': cqtInput
                },
                dataType: "json",
                success: function (data) {
                    if (data.nnt) {
                        updateToUserTabel(data.nnt);
                    }
                }
            });
        } else {
            alert("Vui lòng điền đầy đủ thông tin");
        }    
        $('form#UpdateNNT').trigger("reset");
        $('#UpdateModal').modal('hide');
        return false;
    });

    function updateToUserTabel(nnt) {
        $("#userTable #nnt-" + nnt.id).children(".userData").each(function() {
            var attr = $(this).attr("name");
            if (attr == "ten_nnt") {
              $(this).text(nnt.name);
            } else if (attr == "dia_chi") {
              $(this).text(nnt.dia_chi);
            } else {
              $(this).text(nnt.cqt);
            }
          });
    }
});