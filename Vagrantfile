# -*- mode: ruby -*-
# vi: set ft=ruby sw=2 ts=2 et:

Vagrant.configure("2") do |config|
  config.vm.box = "precise32"
  config.vm.box_url = "http://files.vagrantup.com/precise32.box"
  config.vm.provision "shell", path: "vagrant_provision.py"
  config.vm.provider :virtualbox do |vb|
    name = "dahdi_test"
    vb.customize ["modifyvm", :id, "--uart1", "0x3f8", 4]
    vb.customize ["modifyvm", :id, "--uartmode1", "file", File.expand_path("~/.vagrant.d/tmp/#{name}-S0.txt")]
  end
end
