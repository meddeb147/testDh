import '../controller/password_encryption_controller.dart';
import 'package:get/get.dart';

class PasswordEncryptionBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => PasswordEncryptionController());
  }
}
