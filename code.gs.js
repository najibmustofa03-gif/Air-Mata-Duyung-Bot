function doGet(e) {
  var action = e.parameter.action;
  
  if (action === "getPendingOrders") {
    return getPendingOrders_();
  }
  
  return ContentService.createTextOutput(JSON.stringify({"status": "Active API Endpoint"}))
                       .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var action = data.action;
    
    if (action === "updateStatus") {
      return updateOrderStatus_(data.orderId, data.status);
    }
    
    // Logika simpan pesanan baru dari frontend
    return saveNewOrder_(data);
    
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": error.toString()}))
                         .setMimeType(ContentService.MimeType.JSON);
  }
}

function getActiveSheetByName_(name) {
  // Menggunakan active spreadsheet agar aman dari hardcode ID privat
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  return ss.getSheetByName(name);
}

// Tambahkan fungsi helper parsing multi-produk dengan pemisah semicolon (;) sesuai fitur kuncimu di sini...