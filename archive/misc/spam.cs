Console.WriteLine("Enter your name:");
string name = Console.ReadLine();
Console.WriteLine("Enter the password:");
string password = Console.ReadLine();

if (name == "admin" && password == "1234")
{
    Console.WriteLine("تم الدخول بنجاح");
}
else
{
    Console.WriteLine("فشل في الدخول");
}