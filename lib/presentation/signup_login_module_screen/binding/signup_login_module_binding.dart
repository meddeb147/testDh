import '../controller/signup_login_module_controller.dart';
import 'package:get/get.dart';

class SignupLoginModuleBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => SignupLoginModuleController());
  }
}
