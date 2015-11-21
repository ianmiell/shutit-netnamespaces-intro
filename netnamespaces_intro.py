"""ShutIt module. See http://shutit.tk
"""

from shutit_module import ShutItModule


class netnamespaces_intro(ShutItModule):


	def build(self, shutit):
		# https://www.youtube.com/watch?v=_WgUwUf1d34
		shutit.send('rm -rf /tmp/netnamespaces_intro_vm')
		shutit.send('mkdir -p /tmp/netnamespaces_intro_vm')
		shutit.send('cd /tmp/netnamespaces_intro_vm')
		shutit.send('vagrant init ubuntu/trusty64')
		shutit.send('vagrant up --provider virtualbox')
		shutit.login(command='vagrant ssh')
		shutit.login(command='sudo su -')
		shutit.install('openvswitch-switch')
		shutit.send('ip link',note='Show the network interfaces on the VM')
		shutit.send('ip addr',note='Show the ip address')
		shutit.send('ip route',note='Show the routing table')
		shutit.send('ip netns add red',note='Add the red ip net namespace')
		shutit.send('ip netns add green',note='Add the green ip net namespace')
		shutit.send('ip netns',note='List the network namespaces')
		shutit.send('ls /var/run/netns',note='List the network namespaces by looking directly at the filesystem')
		shutit.send('ip netns add amistake',note='Add the amistake namespace ready to delete')
		shutit.send('ls /var/run/netns',note='List the network namespaces by looking directly at the filesystem')
		shutit.send('ip netns del amistake',note='Delete the mistakenly added network namespace')
		shutit.send('ls /var/run/netns',note='List the network namespaces by looking directly at the filesystem')
		shutit.send('ip netns exec red ip link',note='Run the ip link command from within the red network namespace. Note it is down.')
		# We now use OpenVSwitch to act as a switch for these two network namespaces.
		shutit.send('ovs-vsctl add-br OVS-1',note='Create a network bridge on the host called OVS-1 using openvswitch')
		shutit.send('ovs-vsctl show',note='OVS-1 interface has been added by OpenVSwitch')
		shutit.send('ip link',note='OVS-1 interface has been added')
		# Now to connect these together Root namespace: OVS-1 (->Red, ->Green) - OVS-1 using veth pairs
		# They act like a pipe. 
		shutit.send('ip link add eth0-r type veth peer name veth-r',note='ip link add adds one end (eth0-r) in the red namespace which peers with the other end (veth-r) connected to OVS-1. They are not connected to anything yet')
		shutit.send('ip link',note='The pipe is not connected to anything yet and both ends can be seen in the root namespace')
		shutit.send('ip link set eth0-r netns red',note='Sets the eth0-r link into the red net namespace')
		shutit.send('ip link',note='We cannot see the eth0-r link anymore in the root namespace')
		shutit.send('ip netns exec red ip link',note='It is now in the red net namespace')
		shutit.send('ovs-vsctl add-port OVS-1 veth-r',note='Attach the other end of the veth pair to the virtual switch')
		shutit.send('ovs-vsctl show',note='The veth-r port is now attached to the virtual switch')

		shutit.send('ip link add eth0-g type veth peer name veth-g',note='ip link add adds one end (eth0-g) in the red namespace which peers with the other end (veth-g) connected to OVS-1. They are not connected to anything yet')
		shutit.send('ip link set eth0-g netns green',note='Sets the eth0-g link into the green net namespace')
		shutit.send('ip netns exec green ip link',note='It is now in the green net namespace')
		shutit.send('ovs-vsctl add-port OVS-1 veth-g',note='Attach the other end of the veth pair to the virtual switch')
		# Turn interfaces up and assign IP addresses (10mins into video)
		shutit.send('ip link',note='red namespace linked to OVS-1 in veth-r is DOWN')
		shutit.send('ip link set veth-r up',note='Turn up the veth-r interface')
		shutit.send('ip link',note='red namespace linked to OVS-1 in veth-r is UP')
		shutit.send('ip netns exec red ip link set dev lo up',note='turn up loopback dev in red namespace')
		shutit.send('ip netns exec red ip link set dev eth0-r up',note='turn up dev in red namespace, ie the other end of the veth pipe')
		shutit.send('ip netns exec red ip address add 10.0.0.1/24 dev eth0-r',note='assign an ip address to the end of the veth pair')
		shutit.send('ip netns exec red ip a',note='Interfaces UP and ip address assigned to eth0-r')
		shutit.send('ip netns exec red ip route',note='Network is set up for the namespace')
		shutit.send('ip route',note='Root namespace has no awareness of 10.0.0.0/24. It is isolated')

		shutit.send('ip link set veth-g up',note='Turn up the veth-g interface')
		shutit.send('ip netns exec green ip link set dev lo up',note='turn up loopback dev in green namespace')
		shutit.send('ip netns exec green ip link set dev eth0-g up',note='turn up dev in green namespace, ie the other end of the veth pipe')
		shutit.send('ip netns exec green ip address add 10.0.0.2/24 dev eth0-g',note='assign an ip address to the end of the veth pair')

		shutit.login(command='ip netns exec red bash',note='Enter red network namespace')
		shutit.send('ping -c 3 10.0.0.2',note='We should be able to ping the other network')
		shutit.logout()
		shutit.logout()
		shutit.logout()
		return True

	def get_config(self, shutit):
		# CONFIGURATION
		# shutit.get_config(module_id,option,default=None,boolean=False)
		#                                    - Get configuration value, boolean indicates whether the item is 
		#                                      a boolean type, eg get the config with:
		# shutit.get_config(self.module_id, 'myconfig', default='a value')
		#                                      and reference in your code with:
		# shutit.cfg[self.module_id]['myconfig']
		return True

	def test(self, shutit):
		# For test cycle part of the ShutIt build.
		return True

	def finalize(self, shutit):
		# Any cleanup required at the end.
		return True
	
	def is_installed(self, shutit):
		return False


def module():
	return netnamespaces_intro(
		'shutit.netnamespaces_intro.netnamespaces_intro.netnamespaces_intro', 1259389554.00,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['tk.shutit.vagrant.vagrant.vagrant','shutit-libary.virtualbox.virtualbox.virtualbox']
	)

