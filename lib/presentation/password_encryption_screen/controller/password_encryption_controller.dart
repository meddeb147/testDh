import 'package:aziz_s_application1/core/app_export.dart';
import 'package:aziz_s_application1/presentation/password_encryption_screen/models/password_encryption_model.dart';

class PasswordEncryptionController extends GetxController {
  Rx<PasswordEncryptionModel> passwordEncryptionModelObj =
      PasswordEncryptionModel().obs;

  @override
  void onReady() {
    super.onReady();
  }

  @override
  void onClose() {
    super.onClose();
  }
}
